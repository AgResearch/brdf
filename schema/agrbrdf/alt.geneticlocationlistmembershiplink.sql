--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlistmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (geneticlocationlist) REFERENCES geneticlocationlist(obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationlistmembershiplink
    ADD CONSTRAINT "$2" FOREIGN KEY (geneticlocationfact) REFERENCES geneticlocationfact(obid);


