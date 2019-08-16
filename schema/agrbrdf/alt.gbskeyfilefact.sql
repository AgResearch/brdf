--
-- Name: gbskeyfilefact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilefact_pkey PRIMARY KEY (factid);


--
-- Name: gbskeyfilebiosubjectfk; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilebiosubjectfk FOREIGN KEY (biosubjectob) REFERENCES biosubjectob(obid);


--
-- Name: gbskeyfilefact_barcodedsampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilefact_barcodedsampleob_fkey FOREIGN KEY (barcodedsampleob) REFERENCES biosampleob(obid);


--
-- Name: gbskeyfilefact_biosampleob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gbskeyfilefact
    ADD CONSTRAINT gbskeyfilefact_biosampleob_fkey FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


