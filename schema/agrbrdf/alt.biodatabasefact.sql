--
-- Name: biodatabasefact_biodatabaseob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biodatabasefact
    ADD CONSTRAINT biodatabasefact_biodatabaseob_fkey FOREIGN KEY (biodatabaseob) REFERENCES biodatabaseob(obid);


