--
-- Name: listmembershipfact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY listmembershipfact
    ADD CONSTRAINT listmembershipfact_pkey PRIMARY KEY (factid);


--
-- Name: listmembershipfact_oblist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY listmembershipfact
    ADD CONSTRAINT listmembershipfact_oblist_fkey FOREIGN KEY (oblist) REFERENCES oblist(obid);


