--
-- Name: biolibraryfact_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biolibraryfact
    ADD CONSTRAINT biolibraryfact_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


