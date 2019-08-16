--
-- Name: gbsyieldfact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY gbsyieldfact
    ADD CONSTRAINT gbsyieldfact_pkey PRIMARY KEY (factid);


--
-- Name: gbsyieldfact_biosamplelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbsyieldfact
    ADD CONSTRAINT gbsyieldfact_biosamplelist_fkey FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);


--
-- Name: gbsyieldfact_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbsyieldfact
    ADD CONSTRAINT gbsyieldfact_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


